const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct Table
    {
        const Profile::MESG* lookup[256];
        FIT_UINT16 max_num;

        Table() : max_num(0)
        {
            for (int i = 0; i < MESGS; i++)
            {
                const FIT_UINT16 n = mesgs[i].num;
                if (n < 256 && lookup[n] == NULL)
                    lookup[n] = &mesgs[i];
                if (n > max_num)
                    max_num = n;
            }
        }
    };

    static const Table table;

    if (num < 256)
        return table.lookup[num];

    if (num > table.max_num)
        return NULL;

    for (int i = 0; i < MESGS; i++)
    {
        if (mesgs[i].num == num)
            return &mesgs[i];
    }

    return NULL;
}
