const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const std::vector<const Profile::MESG*> order = []()
    {
        std::vector<const Profile::MESG*> v;
        v.reserve(MESGS);
        for (int i = 0; i < MESGS; i++)
        {
            v.push_back(&mesgs[i]);
        }
        std::stable_sort(v.begin(), v.end(),
            [](const Profile::MESG* a, const Profile::MESG* b)
            {
                return a->num < b->num;
            });
        return v;
    }();

    std::vector<const Profile::MESG*>::const_iterator it =
        std::lower_bound(order.begin(), order.end(), num,
            [](const Profile::MESG* m, FIT_UINT16 value)
            {
                return m->num < value;
            });

    if (it != order.end() && (*it)->num == num)
    {
        return *it;
    }

    return nullptr;
}
