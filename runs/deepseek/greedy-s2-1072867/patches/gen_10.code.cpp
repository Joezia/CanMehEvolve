Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* const data = fields.data();
    const std::size_t n = fields.size();

    std::size_t i = 0;
    for (; i + 1 < n; i += 2)
    {
        if (data[i].GetNum() == fieldNum)
            return &data[i];
        if (data[i + 1].GetNum() == fieldNum)
            return &data[i + 1];
    }
    if (i < n && data[i].GetNum() == fieldNum)
        return &data[i];

    return FIT_NULL;
}
