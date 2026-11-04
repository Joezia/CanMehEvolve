
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::vector<const Profile::MESG*> mesg_by_num;
    static bool initialized = false;
    
    if (!initialized) {
        mesg_by_num.resize(65536, nullptr);
        for (int i = 0; i < MESGS; i++) {
            mesg_by_num[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }
    
    return (num < 65536) ? mesg_by_num[num] : nullptr;
}
