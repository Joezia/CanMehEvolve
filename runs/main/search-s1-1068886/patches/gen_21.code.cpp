
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use static sorted lookup with binary search for O(log n) performance
    static std::vector<FIT_UINT16> sorted_indices = []() {
        std::vector<FIT_UINT16> indices(MESGS);
        for (FIT_UINT16 i = 0; i < MESGS; ++i) indices[i] = i;
        std::sort(indices.begin(), indices.end(), [](FIT_UINT16 a, FIT_UINT16 b) {
            return mesgs[a].num < mesgs[b].num;
        });
        return indices;
    }();

    int left = 0, right = MESGS - 1;
    while (left <= right) {
        int mid = left + ((right - left) >> 1);
        FIT_UINT16 val = mesgs[sorted_indices[mid]].num;
        if (val == num) return &mesgs[sorted_indices[mid]];
        if (val < num) left = mid + 1;
        else right = mid - 1;
    }
    return NULL;
}
