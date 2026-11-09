void Mesg::AddField(const Field& field)
{
    if (fields.empty())
    {
        fields.reserve(16);
        fields.push_back(field);
        return;
    }

    const auto num = field.GetNum();
    const Field* p = fields.data();
    const Field* const end = p + fields.size();
    while (p != end)
    {
        if (p->GetNum() == num)
            return;
        ++p;
    }

    fields.push_back(field);
}
