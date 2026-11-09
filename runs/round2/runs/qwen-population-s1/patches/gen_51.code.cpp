
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::array<const Profile::MESG*, 0x10000> lookup = []() {
        std::array<const Profile::MESG*, 0x10000> arr{};
        for (int i = 0; i < MESGS; i++) {
            arr[mesgs[i].num] = &mesgs[i];
        }
        return arr;
    }();
    return (num < lookup.size()) ? lookup[num] : nullptr;
}
