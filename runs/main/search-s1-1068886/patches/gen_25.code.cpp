
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use static sorted lookup with binary search for O(log n) performance
    static std::vector<FIT_UINT16> sorted_indices = []() {
        std::vector<FIT_UINT16> indices(MESGS);
        std::iota(indices.begin(), indices.end(), 0);
        std::sort(indices.begin(), indices.end(), [](FIT_UINT16 a, FIT_UINT16 b) {
            return mesgs[a].num < mesgs[b].num;
        });
        return indices;
    }();

    // Use std::lower_bound for better branch prediction and potential compiler optimizations
    auto it = std::lower_bound(sorted_indices.begin(), sorted_indices.end(), num,
        [](FIT_UINT16 idx, FIT_UINT16 target) { return mesgs[idx].num < target; });
    
    if (it != sorted_indices.end() && mesgs[*it].num == num) {
        return &mesgs[*it];
    }
    return NULL;
}
