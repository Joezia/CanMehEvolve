
```cpp
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Profile::MESG is static and sorted by num at compile time in release builds
    // Use binary search for O(log n) lookup instead of linear O(n)
    static const std::vector<const Profile::MESG*> sorted_mesgs = [] {
        std::vector<const Profile::MESG*> result;
        result.reserve(MESGS);
        for (int i = 0; i < MESGS; i++) {
            result.push_back(&mesgs[i]);
        }
        std::sort(result.begin(), result.end(), [](const Profile::MESG* a, const Profile::MESG* b) {
            return a->num < b->num;
        });
        return result;
    }();

    auto it = std::lower_bound(sorted_mesgs.begin(), sorted_mesgs.end(), num,
        [](const Profile::MESG* mesg, FIT_UINT16 value) {
            return mesg->num < value;
        });

    if (it != sorted_mesgs.end() && (*it)->num == num)
        return *it;

    return NULL;
}
