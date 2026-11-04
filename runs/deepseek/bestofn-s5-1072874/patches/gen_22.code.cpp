const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    int lo = 0;
    int hi = static_cast<int>(MESGS);

    while (lo < hi)
    {
        const int mid = lo + ((hi - lo) >> 1);
        if (mesgs[mid].num < num)
            lo = mid + 1;
        else
            hi = mid;
    }

    if (lo < static_cast<int>(MESGS) && mesgs[lo].num == num)
        return &mesgs[lo];

    return NULL;
}
