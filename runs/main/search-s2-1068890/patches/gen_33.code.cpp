
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::array<const Profile::MESG*, 65536> index;
    static std::atomic_bool initialized{false};
    
    if (!initialized.load(std::memory_order_acquire)) {
        if (!initialized.exchange(true, std::memory_order_acq_rel)) {
            index.fill(nullptr);
            for (int i = 0; i < MESGS; i++) {
                index[mesgs[i].num] = &mesgs[i];
            }
        }
    }
    return index[num];
}

