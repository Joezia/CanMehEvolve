Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* field = fields.data();
    const auto count = fields.size();

    for (auto i = count; i != 0; --i, ++field)
    {
        if (field->GetNum() == fieldNum)
            return field;
    }

    return FIT_NULL;
}
