const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct Lookup
    {
        const Profile::MESG* table[65536] = {};
        Lookup()
        {
            for (int i = 0; i < MESGS; i++)
            {
                if (table[mesgs[i].num] == NULL)
                    table[mesgs[i].num] = &mesgs[i];
            }
        }
    };
    static Lookup lookup;
    return lookup.table[num];
}
