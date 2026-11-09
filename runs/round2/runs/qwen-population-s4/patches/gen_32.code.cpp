
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num, [](const MESG& m, FIT_UINT16 n) { return m.num < n; });
    return (it != mesgs + MESGS && it->num == num) ? &(*it) : nullptr;
}
