void Mesg::AddField(const Field& field)
{
    const auto num = field.GetNum();
    for (const Field& f : fields)
    {
        if (f.GetNum() == num)
            return;
    }
    if (fields.empty())
        fields.reserve(16);
    fields.push_back(field);
}
