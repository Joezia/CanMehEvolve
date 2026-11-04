
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Linear search is fast for small arrays; unroll and avoid lambda overhead
    for (const Profile::MESG* p = mesgs, *end = mesgs + MESGS; p < end; ++p) {
        if (p->num == num) return p;
    }
    return NULL;
}
