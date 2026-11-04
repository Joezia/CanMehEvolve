const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    int low = 0;
    int high = MESGS - 1;

    while (low <= high)
    {
        const int mid = (low + high) >> 1;
        const FIT_UINT16 mid_num = mesgs[mid].num;

        if (mid_num == num)
            return &mesgs[mid];
        if (mid_num < num)
            low = mid + 1;
        else
            high = mid - 1;
    }

    return NULL;
}
