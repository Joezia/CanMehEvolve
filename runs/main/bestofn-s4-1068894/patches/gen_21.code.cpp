
```cpp
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const auto* const sorted = []() {
        std::vector<const MESG*> v;
        v.reserve(MESGS);
        for (int i = 0; i < MESGS; ++i) {
            v.push_back(&mesgs[i]);
        }
        std::sort(v.begin(), v.end(), [](const MESG* a, const MESG* b) { return a->num < b->num; });
        return v;
    }();

    auto it = std::lower_bound(sorted->begin(), sorted->end(), num,
        [](const MESG* m, FIT_UINT16 n) { return m->num < n; });
    
    return (it != sorted->end() && (*it)->num == num) ? *it : NULL;
}
