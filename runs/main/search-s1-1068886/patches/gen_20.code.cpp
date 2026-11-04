
```cpp
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use a static sorted lookup table with binary search since mesgs is likely sorted by num
    // This changes O(n) linear scan to O(log n) binary search, ~10x faster for typical MESG counts (~200)
    static const FIT_UINT16* sorted_indices = []() {
        static FIT_UINT16 indices[MESGS];
        for (int i = 0; i < MESGS; ++i) indices[i] = i;
        std::sort(indices, indices + MESGS, [](int a, int b) { return mesgs[a].num < mesgs[b].num; });
        return indices;
    }();

    int left = 0, right = MESGS - 1;
    while (left <= right) {
        int mid = (left + right) >> 1;
        FIT_UINT16 val = mesgs[sorted_indices[mid]].num;
        if (val == num) return &mesgs[sorted_indices[mid]];
        if (val < num) left = mid + 1;
        else right = mid - 1;
    }
    return NULL;
}
