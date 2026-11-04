
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::array<const Profile::MESG*, 65536> index;
    static std::atomic_flag initialized = ATOMIC_FLAG_INIT;
    
    if (!initialized.test_and_set(std::memory_order_acquire)) {
        for (int i = 0; i < MESGS; i++) {
            index[mesgs[i].num] = &mesgs[i];
        }
        initialized.test_and_set(std::memory_order_release);
    }
    return index[num];
}
