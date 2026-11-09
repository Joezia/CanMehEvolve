
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search since mesgs is sorted by num (verified by profile initialization)
    // Using std::lower_bound for O(log n) lookup instead of O(n) linear search
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& m, FIT_UINT16 n) { return m.num < n; });
    
    if (it != mesgs + MESGS && it->num == num)
        return it;
    
    return NULL;
}
