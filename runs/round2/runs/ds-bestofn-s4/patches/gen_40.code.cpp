Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* const data = fields.data();
    const auto count = fields.size();
    for (decltype(fields.size()) i = 0; i < count; ++i)
    {
        if (data[i].GetNum() == fieldNum)
            return data + i;
    }

    return FIT_NULL;
}
