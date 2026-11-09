const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct Lookup
    {
        FIT_UINT16 idx[65536] = {};

        Lookup()
        {
            for (int i = 0; i < MESGS; i++)
            {
                FIT_UINT16 n = mesgs[i].num;
                if (idx[n] == 0)
                    idx[n] = static_cast<FIT_UINT16>(i + 1);
            }
        }
    };

    static const Lookup lookup;
    FIT_UINT16 i = lookup.idx[num];
    if (i == 0)
        return NULL;
    return &mesgs[i - 1];
}
