const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static FIT_INT16 s_index[65536];
    static bool s_built = false;
    if (!s_built)
    {
        for (int i = 0; i < 65536; i++)
            s_index[i] = -1;
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (s_index[n] < 0)
                s_index[n] = (FIT_INT16)i;
        }
        s_built = true;
    }

    const FIT_INT16 idx = s_index[num];
    return (idx < 0) ? NULL : &mesgs[idx];
}
