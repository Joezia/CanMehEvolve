
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use binary search since mesgs array is sorted by num (as per FIT spec)
    // Precondition: mesgs array is sorted in ascending order by .num
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& msg, FIT_UINT16 n) { return msg.num < n; });
    
    if (it != mesgs + MESGS && it->num == num)
        return it;
    return NULL;
}
