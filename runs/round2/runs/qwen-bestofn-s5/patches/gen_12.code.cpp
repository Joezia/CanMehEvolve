
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use binary search on sorted mesgs array for O(log n) lookup
    // Assuming mesgs is sorted by num (common pattern for profile data)
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& m, FIT_UINT16 val) { return m.num < val; });
    if (it != mesgs + MESGS && it->num == num)
        return it;
    return NULL;
}
