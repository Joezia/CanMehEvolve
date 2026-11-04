const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* table[65536];
    static const bool initialized = [](const Profile::MESG* m, int count) {
        for (int i = 0; i < 65536; ++i)
            table[i] = NULL;
        for (int i = 0; i < count; ++i)
            if (table[m[i].num] == NULL)
                table[m[i].num] = &m[i];
        return true;
    }(mesgs, MESGS);
    (void)initialized;
    return table[num];
}
