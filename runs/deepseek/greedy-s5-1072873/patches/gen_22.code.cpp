const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* lookup[65536] = {};
    static int max_num = -1;

    if (max_num < 0)
    {
        max_num = 0;
        for (int i = 0; i < MESGS; i++)
        {
            FIT_UINT16 n = mesgs[i].num;
            if (lookup[n] == NULL)
                lookup[n] = &mesgs[i];
            if (n > max_num)
                max_num = n;
        }
    }

    if (num > max_num)
        return NULL;

    return lookup[num];
}
