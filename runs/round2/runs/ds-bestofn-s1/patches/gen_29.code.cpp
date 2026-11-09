const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* table[65536];
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (table[n] == NULL)
                table[n] = &mesgs[i];
        }
        initialized = true;
    }

    return table[num];
}
