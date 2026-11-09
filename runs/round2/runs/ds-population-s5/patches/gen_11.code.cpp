const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct MesgTable
    {
        FIT_UINT16 idx[65536];

        MesgTable()
        {
            for (int i = 0; i < 65536; ++i)
                idx[i] = 0xFFFFu;

            for (int i = 0; i < MESGS; ++i)
            {
                const FIT_UINT16 n = mesgs[i].num;
                if (idx[n] == 0xFFFFu)
                    idx[n] = static_cast<FIT_UINT16>(i);
            }
        }
    };

    static const MesgTable table;
    const FIT_UINT16 i = table.idx[num];

    return (i == 0xFFFFu) ? NULL : &mesgs[i];
}
