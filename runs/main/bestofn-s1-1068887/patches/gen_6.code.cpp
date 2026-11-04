
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use binary search since mesgs array is sorted by num (per profile design)
    // Lower_bound finds first element >= num; check if it matches exactly
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num,
        [](const Profile::MESG& m, FIT_UINT16 val) { return m.num < val; });
    
    if (it != mesgs + MESGS && it->num == num)
        return &*it;
    
    return NULL;
}
