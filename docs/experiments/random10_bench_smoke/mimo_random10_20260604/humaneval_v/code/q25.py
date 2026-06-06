from typing import Dict, List, Tuple

def solution(rectangles: Dict[int, List[Tuple[int, int]]], rectangle_id: int) -> int:
    """
    Calculate the trimmed area of a specified rectangle within a grid.
    """
    if rectangle_id not in rectangles:
        return 0

    # Get the target rectangle coordinates
    target_coords = rectangles[rectangle_id]
    tx1, ty1 = target_coords[0]
    tx2, ty2 = target_coords[1]

    # Calculate the full area of the target rectangle
    target_area = (tx2 - tx1) * (ty2 - ty1)

    # Identify higher priority rectangles (lower ID) that overlap with the target
    # We clip these occluders to the target's bounds since we only care about the area inside target
    occluders = []
    
    for r_id, coords in rectangles.items():
        if r_id < rectangle_id:
            rx1, ry1 = coords[0]
            rx2, ry2 = coords[1]
            
            # Calculate intersection
            ix1 = max(tx1, rx1)
            iy1 = max(ty1, ry1)
            ix2 = min(tx2, rx2)
            iy2 = min(ty2, ry2)
            
            if ix1 < ix2 and iy1 < iy2:
                occluders.append((ix1, iy1, ix2, iy2))

    # If no occluders, return the full area
    if not occluders:
        return target_area

    # Calculate the area of the union of all occluders using Plane Sweep algorithm
    x_vals = set()
    for occ in occluders:
        x_vals.add(occ[0])
        x_vals.add(occ[2])
    
    x_list = sorted(x_vals)
    total_occluded_area = 0
    
    # Sweep through x intervals
    for i in range(len(x_list) - 1):
        x_curr = x_list[i]
        x_next = x_list[i+1]
        strip_width = x_next - x_curr
        
        # Collect active y-intervals for this x-strip
        y_intervals = []
        for occ in occluders:
            ox1, oy1, ox2, oy2 = occ
            if ox1 <= x_curr and ox2 >= x_next:
                y_intervals.append((oy1, oy2))
        
        if y_intervals:
            # Merge y-intervals
            y_intervals.sort()
            merged_y = []
            curr_s, curr_e = y_intervals[0]
            
            for s, e in y_intervals[1:]:
                if s <= curr_e:
                    curr_e = max(curr_e, e)
                else:
                    merged_y.append((curr_s, curr_e))
                    curr_s, curr_e = s, e
            merged_y.append((curr_s, curr_e))
            
            # Calculate covered height
            covered_height = sum(e - s for s, e in merged_y)
            total_occluded_area += strip_width * covered_height
            
    return target_area - total_occluded_area