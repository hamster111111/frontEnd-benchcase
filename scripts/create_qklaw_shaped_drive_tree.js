const cp = require('child_process');

const cli = 'D:/Code/paper-investigate/.npm-global/node_modules/@larksuite/cli/scripts/run.js';

const result = {
  folders: [],
  docs: [],
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function extractJson(text) {
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start < 0 || end < start) {
    throw new Error(`No JSON object found in output:\n${text}`);
  }
  return JSON.parse(text.slice(start, end + 1));
}

async function run(args, retry = 3) {
  for (let attempt = 1; attempt <= retry; attempt += 1) {
    const result = await new Promise((resolve) => {
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
        resolve({ code, stdout, stderr });
      });
    });

    if (result.code === 0) {
      return extractJson(result.stdout);
    }

    const combined = `${result.stdout}\n${result.stderr}`;
    if (combined.includes('99991400') || combined.includes('rate_limit')) {
      const waitMs = 8000 * attempt;
      console.error(`rate limited, retrying in ${waitMs}ms: ${args.join(' ')}`);
      await delay(waitMs);
      continue;
    }

    console.error(`ERR ${args.join(' ')}`);
    console.error(result.stderr || result.stdout);
    throw new Error(`exit ${result.code}`);
  }

  throw new Error(`failed after retries: ${args.join(' ')}`);
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

  if (parent) {
    await run([
      'drive',
      '+move',
      '--as',
      'bot',
      '--type',
      'folder',
      '--file-token',
      data.folder_token,
      '--folder-token',
      parent,
    ]);
  }

  await delay(1200);
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
    // It may already be granted by create-folder.
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

  await run([
    'drive',
    '+move',
    '--as',
    'bot',
    '--type',
    'docx',
    '--file-token',
    token,
    '--folder-token',
    parent,
  ]);
  await makeDocPublic(token);
  await delay(1600);
  return item;
}

function basicDoc(title, sections = ['内容']) {
  return `# ${title}\n\n${sections.map((section) => `## ${section}\n\n- `).join('\n\n')}`;
}

async function createPageNode(node, parentFolder) {
  if (node.children && node.children.length) {
    const folder = await createFolder(node.title, parentFolder);
    await grantFolder(folder.token, await getCurrentUserOpenId());
    await createDoc(node.title, folder.token, basicDoc(node.title, node.sections || ['讨论记录', 'TODO']));
    for (const child of node.children) {
      await createPageNode(child, folder.token);
    }
    return;
  }

  await createDoc(node.title, parentFolder, basicDoc(node.title, node.sections || ['内容', 'TODO']));
}

async function main() {
  const userOpenId = await getCurrentUserOpenId();

  const root = await createFolder('前端 Design Bench（正式版-仿Qklaw树）');
  await grantFolder(root.token, userOpenId);

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

  const sync = await createDoc('冲刺AAAI—同步文档', root.token, syncContent);

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

  await createDoc('前端 Design Bench OnePage', root.token, onepageContent);

  const tree = [
    {
      title: '论文讨论',
      sections: ['整体方向', '写作 TODO'],
      children: [
        {
          title: '整体讨论',
          sections: ['论文主线', '实验闭环'],
          children: [
            {
              title: '当前论文 | 前端 Design Bench：评测、失败分析与优化框架',
              sections: ['摘要草稿', '核心贡献', '实验安排'],
            },
            {
              title: '实验计划',
              sections: ['benchmark 选择', '模型与框架', '消融实验'],
            },
          ],
        },
        { title: 'Failure分析', sections: ['低分 case', '失败模式', '改进方向'] },
        { title: 'Failure归类相关文献', sections: ['论文列表', '分类体系', '可借鉴点'] },
        { title: 'TakeAway', sections: ['观察', '结论', '下一步'] },
        { title: '论文介绍', sections: ['背景', '方法', '实验'] },
        { title: 'references参考文献收集', sections: ['前端生成', 'GUI/Vision Benchmark', 'Agent/Framework'] },
      ],
    },
    {
      title: '协作',
      sections: ['协作规则', '同步节奏'],
      children: [{ title: '任务分工', sections: ['李昱辰', '朱盛杰', '林景豪'] }],
    },
    {
      title: '仓库review',
      sections: ['仓库列表', '复现状态'],
      children: [{ title: 'Bench', sections: ['可跑 benchmark', '环境要求', '运行命令'] }],
    },
    { title: '竞品分析文档', sections: ['相关方法', '对比维度', '可借鉴点'] },
    { title: '前端实验', sections: ['实验批次', '结果记录', 'case 分析'] },
  ];

  for (const node of tree) {
    await createPageNode(node, root.token);
  }

  console.log(`RESULT_JSON:${JSON.stringify(result)}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
