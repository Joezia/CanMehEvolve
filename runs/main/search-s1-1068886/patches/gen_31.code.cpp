
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Precomputed sorted indices at compile time via static constexpr array
    // Use std::lower_bound for faster binary search with branch prediction optimization
    static const std::array<FIT_UINT16, MESGS> sorted_indices = []() {
        std::array<FIT_UINT16, MESGS> indices;
        for (FIT_UINT16 i = 0; i < MESGS; ++i) indices[i] = i;
        std::sort(indices.begin(), indices.end(), [](FIT_UINT16 a, FIT_UINT16 b) {
            return mesgs[a].num < mesgs[b].num;
        });
        return indices;
    }();

    auto it = std::lower_bound(sorted_indices.begin(), sorted_indices.end(), num,
        [](FIT_UINT16 idx, FIT_UINT16 target) {
            return mesgs[idx].num < target;
        });

    if (it != sorted_indices.end() && mesgs[*it].num == num) {
        return &mesgs[*it];
    }
    return NULL;
}
