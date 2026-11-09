
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use binary search since mesgs array is sorted by num (per FIT spec and implementation)
    // Binary search reduces O(n) to O(log n), which is faster for typical MESG counts (~50-100)
    const auto* first = mesgs;
    const auto* last = mesgs + MESGS;
    const auto* it = std::lower_bound(first, last, num, 
        [](const Profile::MESG& mesg, FIT_UINT16 value) { return mesg.num < value; });
    
    if (it != last && it->num == num)
        return &(*it);
    return NULL;
}
