
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search since mesgs array is sorted by num (per FIT spec)
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const MESG& m, FIT_UINT16 n) { return m.num < n; });
    
    if (it != mesgs + MESGS && it->num == num)
        return &(*it);
    
    return NULL;
}
