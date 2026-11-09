
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search since mesgs is sorted by num (verified by profile initialization)
    // Use lower_bound to find first element >= num, then check equality
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& m, FIT_UINT16 n) { return m.num < n; });
    
    if (it != mesgs + MESGS && it->num == num)
        return it;
    
    return NULL;
}
