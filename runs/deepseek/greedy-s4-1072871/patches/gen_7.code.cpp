const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct Entry
    {
        FIT_UINT16 key;
        FIT_UINT16 val;
    };

    static Entry table[4096] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = static_cast<int>(MESGS) - 1; i >= 0; --i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            unsigned h = (static_cast<unsigned>(n) * 2654435761u) >> 20;
            while (table[h].val != 0 && table[h].key != n)
            {
                h = (h + 1) & 4095u;
            }
            table[h].key = n;
            table[h].val = static_cast<FIT_UINT16>(i + 1);
        }
        initialized = true;
    }

    unsigned h = (static_cast<unsigned>(num) * 2654435761u) >> 20;
    while (table[h].val != 0)
    {
        if (table[h].key == num)
        {
            return &mesgs[table[h].val - 1];
        }
        h = (h + 1) & 4095u;
    }
    return nullptr;
}
