
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use binary search since mesgs array is sorted by num (per FIT spec)
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const MESG& msg, FIT_UINT16 n) { return msg.num < n; });
    if (it != mesgs + MESGS && it->num == num)
        return it;
    return NULL;
}
