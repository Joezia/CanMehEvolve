Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* const data = fields.data();
    const auto count = fields.size();

    for (decltype(count) i = 0; i < count; ++i)
    {
        Field& field = data[i];
        if (field.GetNum() == fieldNum)
            return &field;
    }

    return FIT_NULL;
}
