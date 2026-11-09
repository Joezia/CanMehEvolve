
DeveloperFieldDefinition::~DeveloperFieldDefinition()
{
    delete mesg;
    mesg = nullptr;
    delete developer;
    developer = nullptr;
}
