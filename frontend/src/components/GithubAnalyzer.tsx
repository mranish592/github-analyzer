import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

// Define interfaces for our data structures
interface ExperienceItem {
  language: string;
  linesOfCode: number;
  repositories: number;
  usingSince: string;
}

interface CodeQualityItem {
  language: string;
  reliabilityRating: string;
  securityRating: string;
  maintainabilityRating: string;
  duplicatedLinesDensity: string;
  vulnerabilityPerCommit: number;
  bugsPerCommit: number;
  codeSmellsPerCommit: number;
}

interface ScanResult {
  experience: ExperienceItem[];
  codeQuality: CodeQualityItem[];
}

type ScanType = 'quick' | 'deep';

export default function GitHubAnalyzer() {
  const [username, setUsername] = useState<string>('');
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  
  // Mock data - in a real app this would come from your API
  const experienceData: ExperienceItem[] = [
    {
      language: 'Kotlin',
      linesOfCode: 400,
      repositories: 3,
      usingSince: '1 Month'
    },
    {
      language: 'Python',
      linesOfCode: 600,
      repositories: 5,
      usingSince: '3 Years'
    },
    {
      language: 'FastAPI',
      linesOfCode: 200,
      repositories: 2,
      usingSince: '2 Months'
    }
  ];

  const codeQualityData: CodeQualityItem[] = [
    {
      language: 'Kotlin',
      reliabilityRating: 'A',
      securityRating: 'A',
      maintainabilityRating: 'B',
      duplicatedLinesDensity: '20%',
      vulnerabilityPerCommit: 2,
      bugsPerCommit: 1,
      codeSmellsPerCommit: 0.5
    },
    {
      language: 'Python',
      reliabilityRating: 'A',
      securityRating: 'A',
      maintainabilityRating: 'B',
      duplicatedLinesDensity: '20%',
      vulnerabilityPerCommit: 2,
      bugsPerCommit: 1,
      codeSmellsPerCommit: 0.5
    },
    {
      language: 'FastAPI',
      reliabilityRating: 'A',
      securityRating: 'A',
      maintainabilityRating: 'B',
      duplicatedLinesDensity: '20%',
      vulnerabilityPerCommit: 2,
      bugsPerCommit: 1,
      codeSmellsPerCommit: 0.5
    }
  ];

  const startScan = (type: ScanType): void => {
    setIsScanning(true);
    setProgress(0);
    
    // Simulate progress for demonstration
    const interval = setInterval(() => {
      setProgress((prevProgress) => {
        const newProgress = prevProgress + 10;
        if (newProgress >= 100) {
          clearInterval(interval);
          setIsScanning(false);
          return 100;
        }
        return newProgress;
      });
    }, 500);
    
    // In a real app, you'd call your API here
    // fetchData(username, type).then((data: ScanResult) => {
    //   // Process data
    //   setIsScanning(false);
    // });
  };

  const getRatingColor = (rating: string): string => {
    switch(rating) {
      case 'A': return 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200';
      case 'B': return 'bg-blue-100 text-blue-800 hover:bg-blue-200';
      case 'C': return 'bg-amber-100 text-amber-800 hover:bg-amber-200';
      case 'D': return 'bg-orange-100 text-orange-800 hover:bg-orange-200';
      default: return 'bg-red-100 text-red-800 hover:bg-red-200';
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">GitHub Analyzer</h1>
      
      <div className="flex gap-4 mb-6">
        <Input 
          placeholder="Enter GitHub username" 
          value={username}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
          className="flex-grow"
        />
        <Button 
          onClick={() => startScan('quick')}
          disabled={isScanning || !username}
          className="text-white bg-gradient-to-br from-teal-600 to-teal-700 shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:shadow-none"
        >
          Quick Scan
        </Button>
        <Button 
          onClick={() => startScan('deep')}
          disabled={isScanning || !username}
          className="text-white bg-gradient-to-br from-slate-600 to-slate-700 shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:shadow-none"
        >
          Deep Scan
        </Button>
      </div>
      
      {isScanning && (
        <div className="mb-6">
          <p className="text-sm text-gray-500 mb-2">Scanning in progress...</p>
          <Progress value={progress} className="h-2" />
        </div>
      )}
      
      <Tabs defaultValue="experience" className="mt-8">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="experience">Experience</TabsTrigger>
          <TabsTrigger value="codeQuality">Code Quality</TabsTrigger>
        </TabsList>
        
        <TabsContent value="experience">
          <Card className="shadow-sm">
            <CardHeader className="bg-gray-50">
              <CardTitle>Experience</CardTitle>
            </CardHeader>
            <CardContent>
              {experienceData.map((item, index) => (
                <div key={index} className="mb-6 pb-6 border-b last:border-0">
                  <h3 className="text-xl font-semibold mb-3">{item.language}</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Lines of code written</p>
                      <p className="font-medium">{item.linesOfCode.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Repositories</p>
                      <p className="font-medium">{item.repositories}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Using since</p>
                      <p className="font-medium">{item.usingSince}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="codeQuality">
          <Card className="shadow-sm">
            <CardHeader className="bg-gray-50">
              <CardTitle>Code Quality</CardTitle>
            </CardHeader>
            <CardContent>
              {codeQualityData.map((item, index) => (
                <div key={index} className="mb-8 pb-6 border-b last:border-0">
                  <h3 className="text-xl font-semibold mb-4">{item.language}</h3>
                  <div className="grid grid-cols-2 gap-6 mb-4">
                    <div className="flex items-center">
                      <p className="text-sm text-gray-500 mr-2">Reliability Rating:</p>
                      <Badge className={`${getRatingColor(item.reliabilityRating)}`}>
                        {item.reliabilityRating}
                      </Badge>
                    </div>
                    <div className="flex items-center">
                      <p className="text-sm text-gray-500 mr-2">Security Rating:</p>
                      <Badge className={`${getRatingColor(item.securityRating)}`}>
                        {item.securityRating}
                      </Badge>
                    </div>
                    <div className="flex items-center">
                      <p className="text-sm text-gray-500 mr-2">Maintainability Rating:</p>
                      <Badge className={`${getRatingColor(item.maintainabilityRating)}`}>
                        {item.maintainabilityRating}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Duplicated Lines Density:</p>
                      <p className="font-medium">{item.duplicatedLinesDensity}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Vulnerability per commit:</p>
                      <p className="font-medium">{item.vulnerabilityPerCommit}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Bugs per commit:</p>
                      <p className="font-medium">{item.bugsPerCommit}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Code Smells per commit:</p>
                      <p className="font-medium">{item.codeSmellsPerCommit}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}