
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search since mesgs array is sorted by num (per FIT spec)
    const Profile::MESG* begin = mesgs;
    const Profile::MESG* end = mesgs + MESGS;
    const Profile::MESG* it = std::lower_bound(begin, end, num,
        [](const Profile::MESG& mesg, FIT_UINT16 value) { return mesg.num < value; });
    
    if (it != end && it->num == num)
        return it;
    return NULL;
}
