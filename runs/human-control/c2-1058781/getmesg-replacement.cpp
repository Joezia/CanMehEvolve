const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct LookupTable
    {
        const MESG* byNumber[65536] = {};

        LookupTable()
        {
            for (int i = 0; i < MESGS; ++i)
            {
                const FIT_UINT16 messageNumber = mesgs[i].num;
                if (byNumber[messageNumber] == NULL)
                    byNumber[messageNumber] = &mesgs[i];
            }
        }
    };

    static const LookupTable table;
    return table.byNumber[num];
}
