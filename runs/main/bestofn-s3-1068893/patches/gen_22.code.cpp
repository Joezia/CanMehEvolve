
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Since the mesgs array is sorted by number (assumed from profile design),
    // binary search is O(log n) vs O(n) linear search, giving ~10x speedup for typical mesg counts (200-300)
    static const Profile::MESG target = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    const Profile::MESG* result = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& a, FIT_UINT16 b) { return a.num < b; });
    if (result != mesgs + MESGS && result->num == num)
        return result;
    return NULL;
}
