
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* cached = nullptr;
    if (cached && cached->num == num) {
        return cached;
    }

    // Binary search on sorted mesgs array
    const Profile::MESG* first = mesgs;
    const Profile::MESG* last = mesgs + MESGS;

    while (first < last) {
        const Profile::MESG* mid = first + ((last - first) >> 1);
        if (mid->num < num) {
            first = mid + 1;
        } else if (mid->num > num) {
            last = mid;
        } else {
            cached = mid;
            return mid;
        }
    }

    return NULL;
}
