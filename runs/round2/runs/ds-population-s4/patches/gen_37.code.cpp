void Mesg::AddField(const Field& field)
{
    const auto num = field.GetNum();

    if (fields.empty())
    {
        fields.reserve(16);
        fields.push_back(field);
        return;
    }

    const Field* data = fields.data();
    const auto count = fields.size();
    for (decltype(count) i = 0; i < count; ++i)
    {
        if (data[i].GetNum() == num)
            return;
    }

    fields.push_back(field);
}
