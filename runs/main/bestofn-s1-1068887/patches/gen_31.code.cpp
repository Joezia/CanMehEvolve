
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Use a precomputed lookup table for O(1) access since message numbers are small and sparse
    // Assuming MESG numbers fit in a reasonable range (e.g., < 1024), we use direct indexing
    static std::array<const Profile::MESG*, 1024> lookup_table = []{
        std::array<const Profile::MESG*, 1024> table{};
        for (int i = 0; i < MESGS; i++)
        {
            if (mesgs[i].num < 1024)
                table[mesgs[i].num] = &mesgs[i];
        }
        return table;
    }();

    if (num < 1024)
        return lookup_table[num];
    return NULL;
}
