const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    int lo = 0;
    int hi = MESGS - 1;

    while (lo <= hi)
    {
        const int mid = lo + ((hi - lo) >> 1);
        const FIT_UINT16 mid_num = mesgs[mid].num;

        if (mid_num == num)
            return &mesgs[mid];

        if (mid_num < num)
            lo = mid + 1;
        else
            hi = mid - 1;
    }

    return NULL;
}
