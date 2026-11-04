
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& m, FIT_UINT16 val) { return m.num < val; });
    return (it != mesgs + MESGS && it->num == num) ? it : NULL;
}
