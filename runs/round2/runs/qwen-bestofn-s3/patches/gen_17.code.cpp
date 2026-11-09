
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::vector<const Profile::MESG*> indexed;
    if (indexed.empty()) {
        indexed.resize(65536, nullptr);
        for (int i = 0; i < MESGS; i++) {
            indexed[mesgs[i].num] = &mesgs[i];
        }
    }
    return indexed[num];
}
