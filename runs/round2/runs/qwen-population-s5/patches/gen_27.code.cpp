
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search over sorted mesgs array for O(log n) lookup
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& m, FIT_UINT16 val) { return m.num < val; });
    if (it != mesgs + MESGS && it->num == num)
        return it;
    return NULL;
}
