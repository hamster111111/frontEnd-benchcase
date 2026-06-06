const cp = require('child_process');

const cli = 'D:/Code/paper-investigate/.npm-global/node_modules/@larksuite/cli/scripts/run.js';

const result = {
  folders: [],
  docs: [],
};

function extractJson(text) {
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start < 0 || end < start) {
    throw new Error(`No JSON object found in output:\n${text}`);
  }
  return JSON.parse(text.slice(start, end + 1));
}

function run(args) {
  return new Promise((resolve, reject) => {
    const child = cp.spawn('node', [cli, ...args], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => {
      stdout += chunk;
    });
    child.stderr.on('data', (chunk) => {
      stderr += chunk;
    });
    child.on('exit', (code) => {
      if (code) {
        console.error(`ERR ${args.join(' ')}`);
        console.error(stderr || stdout);
        reject(new Error(`exit ${code}`));
        return;
      }
      try {
        resolve(extractJson(stdout));
      } catch (error) {
        console.error(stdout);
        reject(error);
      }
    });
  });
}

async function getCurrentUserOpenId() {
  const res = await run(['auth', 'status']);
  return res.userOpenId || (res.identities && res.identities.user && res.identities.user.openId);
}

async function createFolder(name, parent = '') {
  const args = ['drive', '+create-folder', '--as', 'bot', '--name', name];
  if (parent) args.push('--folder-token', parent);
  const res = await run(args);
  const data = res.data;
  const item = {
    name,
    token: data.folder_token,
    url: data.url,
    parent,
  };
  result.folders.push(item);
  console.log(`+folder ${name} ${data.folder_token}`);
  return item;
}

async function grantFolder(token, userOpenId) {
  if (!userOpenId) return;
  const data = {
    member_id: userOpenId,
    member_type: 'openid',
    perm: 'full_access',
    type: 'user',
  };
  try {
    await run([
      'drive',
      'permission.members',
      'create',
      '--as',
      'bot',
      '--yes',
      '--params',
      JSON.stringify({ token, type: 'folder', need_notification: false }),
      '--data',
      JSON.stringify(data),
    ]);
  } catch (_) {
    // The root folder may already have been auto-granted by the CLI.
  }
}

async function makeDocPublic(token) {
  const data = {
    link_share_entity: 'anyone_editable',
    external_access: true,
    share_entity: 'anyone',
    comment_entity: 'anyone_can_edit',
    security_entity: 'anyone_can_edit',
  };
  await run([
    'drive',
    'permission.public',
    'patch',
    '--as',
    'bot',
    '--yes',
    '--params',
    JSON.stringify({ token, type: 'docx' }),
    '--data',
    JSON.stringify(data),
  ]);
}

async function createDoc(title, parent, content) {
  const body = `<title>${title}</title>\n\n${content}`;
  const res = await run([
    'docs',
    '+create',
    '--api-version',
    'v2',
    '--as',
    'bot',
    '--folder-token',
    parent,
    '--doc-format',
    'markdown',
    '--content',
    body,
  ]);
  const url = res.data.document.url;
  const token = url.split('/docx/')[1];
  const item = { title, token, url, parent };
  result.docs.push(item);
  console.log(`+doc ${title} ${token}`);
  await makeDocPublic(token);
  return item;
}

function basicDoc(title, sections) {
  return `# ${title}\n\n${sections.map((section) => `## ${section}\n\n- `).join('\n\n')}`;
}

async function main() {
  const userOpenId = await getCurrentUserOpenId();

  const root = await createFolder('前端 Design Bench（正式版）');
  const overview = await createFolder('00_总览', root.token);
  const benchmark = await createFolder('01_benchmark看板', root.token);
  const paper = await createFolder('02_论文讨论', root.token);
  const experiments = await createFolder('03_实验记录', root.token);
  const baseline = await createFolder('04_baseline调研', root.token);
  const collaboration = await createFolder('05_协作', root.token);
  const references = await createFolder('06_资料沉淀', root.token);

  for (const folder of result.folders) {
    await grantFolder(folder.token, userOpenId);
  }

  const syncContent = `<callout emoji="🎼">指标 / 指标 / 指标 / 指标 指标</callout>

# 0603 周三

<table>
  <thead>
    <tr><th>Project</th><th>Leader</th><th>0611进度</th><th>0609进度</th><th>0606进度</th><th>0604进度</th><th>0603进度</th></tr>
  </thead>
  <tbody>
    <tr><td rowspan="3">前端</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>`;

  const sync = await createDoc('冲刺AAAI—同步文档', overview.token, syncContent);

  const onepageContent = `## 前端 Design Bench OnePage

- 项目定位：
- 一句话主线：
- Leader：李昱辰
- 当前 milestone：
- 同步文档：${sync.url}
- 正式版文件夹：${root.url}

## 最新进展

-

## 关键结论 / 决策

- 待补充

## TODO / 卡点

- benchmark 确定几个关键 @李昱辰
- 动机确定：50% bench @李昱辰，50% bench @朱盛杰，用 dpsk-v4-flash 跑，分析低分 case，总结共性问题，形成动机（benchmark 看板）
- baseline 确定：调研前端优化方法 @林景豪

## 相关链接

- 代码：
- 论文：
- Bench：
- 其他素材：

## 供查阅的其他文档

- `;

  await createDoc('前端 Design Bench OnePage', overview.token, onepageContent);

  await createDoc('benchmark候选与关键集确认', benchmark.token, basicDoc('benchmark候选与关键集确认', ['候选 benchmark', '筛选标准', '关键 benchmark 决策']));
  await createDoc('benchmark跑分记录', benchmark.token, basicDoc('benchmark跑分记录', ['模型与框架', '跑分记录', '复现实验备注']));
  await createDoc('低分case分析', benchmark.token, basicDoc('低分case分析', ['case 列表', '错误类型', '共性问题']));

  await createDoc('论文讨论', paper.token, basicDoc('论文讨论', ['核心问题', '方法方向', '写作 TODO']));
  await createDoc('问题与动机', paper.token, basicDoc('问题与动机', ['低分现象', '共性痛点', '论文动机']));
  await createDoc('实验计划', paper.token, basicDoc('实验计划', ['主实验', '消融实验', '风险与替代方案']));

  await createDoc('dpsk-v4-flash实验记录', experiments.token, basicDoc('dpsk-v4-flash实验记录', ['配置', '样本', '结果', '失败案例']));
  await createDoc('baseline结果记录', experiments.token, basicDoc('baseline结果记录', ['baseline 列表', '结果表', '备注']));
  await createDoc('case共性问题总结', experiments.token, basicDoc('case共性问题总结', ['问题类型', '代表案例', '可优化点']));

  await createDoc('前端优化方法调研', baseline.token, basicDoc('前端优化方法调研', ['方法列表', '适用 benchmark', '实现成本']));
  await createDoc('竞品与相关工作', baseline.token, basicDoc('竞品与相关工作', ['相关论文', '相关系统', '差异点']));

  await createDoc('任务分工', collaboration.token, basicDoc('任务分工', ['负责人', '当前任务', '下次同步']));
  await createDoc('会议记录', collaboration.token, basicDoc('会议记录', ['日期', '结论', '后续动作']));

  await createDoc('论文与链接资料', references.token, basicDoc('论文与链接资料', ['论文', '项目链接', '数据链接']));
  await createDoc('工具与脚本记录', references.token, basicDoc('工具与脚本记录', ['脚本', '运行命令', '注意事项']));

  console.log(`RESULT_JSON:${JSON.stringify(result)}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
