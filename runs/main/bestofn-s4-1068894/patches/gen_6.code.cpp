
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search requires sorted mesgs array; assuming profile data is sorted by num
    auto it = std::lower_bound(mesgs, mesgs + MESGS, num, 
        [](const Profile::MESG& m, FIT_UINT16 val) { return m.num < val; });
    
    if (it != mesgs + MESGS && it->num == num)
        return &(*it);
    return NULL;
}
