
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use binary search since mesgs array is sorted by num (verified from profile data)
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& mesg, FIT_UINT16 val) { return mesg.num < val; });
    if (it != mesgs + MESGS && it->num == num)
        return &(*it);
    return NULL;
}
